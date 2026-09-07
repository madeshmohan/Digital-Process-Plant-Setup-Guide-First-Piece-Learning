from typing import Dict, Any, Tuple

PRODUCT_SPECS = {
    "Variant A": {
        "target_temperature": 180.0,
        "min_temperature": 175.0,
        "max_temperature": 185.0,
        "target_pressure": 5.0,
        "min_pressure": 4.7,
        "max_pressure": 5.3,
    },
    "Variant B": {
        "target_temperature": 195.0,
        "min_temperature": 190.0,
        "max_temperature": 200.0,
        "target_pressure": 5.5,
        "min_pressure": 5.2,
        "max_pressure": 5.8,
    },
    "Variant C": {
        "target_temperature": 210.0,
        "min_temperature": 205.0,
        "max_temperature": 215.0,
        "target_pressure": 6.0,
        "min_pressure": 5.7,
        "max_pressure": 6.3,
    },
    "Variant D": {
        "target_temperature": 220.0,
        "min_temperature": 215.0,
        "max_temperature": 225.0,
        "target_pressure": 6.5,
        "min_pressure": 6.2,
        "max_pressure": 6.8,
    },
}

def validate_parameters(variant: str, temp: float, pressure: float) -> Dict[str, Any]:
    spec = PRODUCT_SPECS.get(variant)
    if not spec:
        return {
            "product_variant": variant,
            "temperature": temp,
            "pressure": pressure,
            "temp_valid": False,
            "pressure_valid": False,
            "interaction_valid": False,
            "interaction_score": 999.0,
            "status": "BLOCKED",
            "reason": f"Unknown product variant: {variant}",
            "temp_deviation": 0.0,
            "pressure_deviation": 0.0
        }

    t_target = spec["target_temperature"]
    t_min = spec["min_temperature"]
    t_max = spec["max_temperature"]
    t_tol = t_max - t_target  # e.g. 5.0

    p_target = spec["target_pressure"]
    p_min = spec["min_pressure"]
    p_max = spec["max_pressure"]
    p_tol = p_max - p_target  # e.g. 0.3

    temp_valid = (t_min <= temp <= t_max)
    pressure_valid = (p_min <= pressure <= p_max)

    t_dev = temp - t_target
    p_dev = pressure - p_target

    # Normalized deviations [-1.0, 1.0]
    x = t_dev / t_tol if t_tol > 0 else 0.0
    y = p_dev / p_tol if p_tol > 0 else 0.0

    # Interaction formula with positive coupling term
    interaction_score = (x ** 2) + (y ** 2) + (0.6 * x * y)
    interaction_valid = (interaction_score <= 1.0)

    # Determine status and human readable rationale
    if not temp_valid:
        status = "BLOCKED"
        reason = f"BLOCKED: Temperature {temp:.1f}°C is outside the configured synthetic range [{t_min:.1f}°C - {t_max:.1f}°C] for {variant}."
    elif not pressure_valid:
        status = "BLOCKED"
        reason = f"BLOCKED: Pressure {pressure:.2f} bar is outside the configured synthetic range [{p_min:.2f} bar - {p_max:.2f} bar] for {variant}."
    elif not interaction_valid:
        status = "BLOCKED"
        reason = (
            f"BLOCKED (Interaction Failure): Temperature ({temp:.1f}°C) and Pressure ({pressure:.2f} bar) "
            f"are individually inside allowed limits, but their combined interaction score ({interaction_score:.2f}) "
            f"exceeds the safe envelope limit (1.00). High temperature combined with high pressure causes thermal-pressure stress violation."
        )
    elif interaction_score > 0.75:
        status = "WARNING"
        reason = (
            f"WARNING: Parameters within individual limits, but operating near the boundary of the safe "
            f"temperature-pressure interaction envelope (score: {interaction_score:.2f} / 1.00). Exercise caution during stabilization."
        )
    else:
        status = "VALID"
        reason = f"VALID: Temperature ({temp:.1f}°C) and Pressure ({pressure:.2f} bar) combination is within the validated operating window."

    return {
        "product_variant": variant,
        "temperature": temp,
        "pressure": pressure,
        "temp_valid": temp_valid,
        "pressure_valid": pressure_valid,
        "interaction_valid": interaction_valid,
        "interaction_score": round(interaction_score, 4),
        "status": status,
        "reason": reason,
        "temp_deviation": round(t_dev, 2),
        "pressure_deviation": round(p_dev, 3),
        "min_temperature": t_min,
        "max_temperature": t_max,
        "min_pressure": p_min,
        "max_pressure": p_max,
        "target_temperature": t_target,
        "target_pressure": p_target
    }
