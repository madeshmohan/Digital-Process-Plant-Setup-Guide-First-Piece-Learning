import sqlite3
from typing import Dict, Any
from backend.database.database import get_db_connection
from backend.validation.validation_engine import PRODUCT_SPECS

SAFETY_DISCLAIMER = (
    "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results "
    "are synthetic demonstration assumptions and must not be used as real plant operating instructions."
)

def get_recommendations_for_variant(variant: str) -> Dict[str, Any]:
    spec = PRODUCT_SPECS.get(variant)
    if not spec:
        return {
            "product_variant": variant,
            "recommended_temperature": 0.0,
            "recommended_pressure": 0.0,
            "sample_size": 0,
            "historical_pass_rate": 0.0,
            "min_safe_temp": 0.0,
            "max_safe_temp": 0.0,
            "min_safe_pressure": 0.0,
            "max_safe_pressure": 0.0,
            "confidence_level": "Low",
            "disclaimer": SAFETY_DISCLAIMER
        }

    t_target = spec["target_temperature"]
    t_min = spec["min_temperature"]
    t_max = spec["max_temperature"]
    p_target = spec["target_pressure"]
    p_min = spec["min_pressure"]
    p_max = spec["max_pressure"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total setups for this variant with inspection
    cursor.execute("""
        SELECT COUNT(*) as total_count,
               SUM(CASE WHEN fpi.pass_fail = 1 THEN 1 ELSE 0 END) as pass_count
        FROM setups s
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        WHERE s.product_variant = ?
    """, (variant,))
    stats_row = cursor.fetchone()
    total_count = stats_row["total_count"] if stats_row and stats_row["total_count"] else 0
    pass_count = stats_row["pass_count"] if stats_row and stats_row["pass_count"] else 0

    pass_rate = round((pass_count / total_count * 100.0), 1) if total_count > 0 else 0.0

    # Query successful setups
    cursor.execute("""
        SELECT AVG(sp.temperature) as avg_temp, AVG(sp.pressure) as avg_pressure, COUNT(*) as sample_count
        FROM setups s
        JOIN setup_parameters sp ON s.setup_id = sp.setup_id
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        WHERE s.product_variant = ? AND fpi.pass_fail = 1 AND sp.validation_status IN ('VALID', 'WARNING')
    """, (variant,))
    row = cursor.fetchone()

    sample_size = row["sample_count"] if row and row["sample_count"] is not None else 0
    if sample_size > 0 and row["avg_temp"] is not None:
        calc_temp = round(row["avg_temp"], 1)
        calc_press = round(row["avg_pressure"], 2)
    else:
        calc_temp = t_target
        calc_press = p_target

    # Ensure recommendations NEVER exceed safe bounds
    rec_temp = max(t_min, min(t_max, calc_temp))
    rec_press = max(p_min, min(p_max, calc_press))

    if sample_size >= 30:
        confidence = "High Confidence (30+ Successful Setups)"
    elif sample_size >= 10:
        confidence = "Moderate Confidence (10-29 Successful Setups)"
    else:
        confidence = "Low / Initial Estimate (< 10 Setups)"

    conn.close()

    return {
        "product_variant": variant,
        "recommended_temperature": rec_temp,
        "recommended_pressure": rec_press,
        "sample_size": sample_size,
        "historical_pass_rate": pass_rate,
        "min_safe_temp": t_min,
        "max_safe_temp": t_max,
        "min_safe_pressure": p_min,
        "max_safe_pressure": p_max,
        "confidence_level": confidence,
        "disclaimer": SAFETY_DISCLAIMER
    }
