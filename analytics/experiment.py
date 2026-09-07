from typing import Dict, Any, List
from backend.database.database import get_db_connection

SAFETY_DISCLAIMER = (
    "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results "
    "are synthetic demonstration assumptions and must not be used as real plant operating instructions."
)

def run_experiment_analysis() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query metrics grouped by is_prototype (0 = Baseline, 1 = Prototype)
    cursor.execute("""
        SELECT 
            s.is_prototype,
            COUNT(*) as total_setups,
            AVG(s.setup_time_minutes) as avg_setup_time,
            SUM(CASE WHEN fpi.pass_fail = 0 THEN 1 ELSE 0 END) as total_failures,
            SUM(CASE WHEN fpi.pass_fail = 1 THEN 1 ELSE 0 END) as total_passes,
            AVG(pm.rework_required) * 100.0 as rework_rate,
            AVG(pm.material_waste_kg) as avg_waste_kg,
            SUM(CASE WHEN sp.validation_status = 'BLOCKED' THEN 1 ELSE 0 END) as blocked_validations
        FROM setups s
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        JOIN setup_parameters sp ON s.setup_id = sp.setup_id
        JOIN performance_metrics pm ON s.setup_id = pm.setup_id
        GROUP BY s.is_prototype
    """)
    rows = cursor.fetchall()

    group_data = {}
    for r in rows:
        key = "prototype" if r["is_prototype"] == 1 else "baseline"
        total = r["total_setups"]
        failures = r["total_failures"]
        passes = r["total_passes"]
        defect_rate = (failures / total * 100.0) if total > 0 else 0.0
        pass_rate = (passes / total * 100.0) if total > 0 else 0.0

        group_data[key] = {
            "total_setups": total,
            "avg_setup_time_mins": round(r["avg_setup_time"], 2) if r["avg_setup_time"] else 0.0,
            "total_failures": failures,
            "total_passes": passes,
            "defect_rate_pct": round(defect_rate, 2),
            "pass_rate_pct": round(pass_rate, 2),
            "rework_rate_pct": round(r["rework_rate"], 2) if r["rework_rate"] else 0.0,
            "avg_waste_kg": round(r["avg_waste_kg"], 2) if r["avg_waste_kg"] else 0.0,
            "blocked_validations": r["blocked_validations"]
        }

    base = group_data.get("baseline", {
        "total_setups": 0, "avg_setup_time_mins": 0.0, "defect_rate_pct": 0.0,
        "pass_rate_pct": 0.0, "rework_rate_pct": 0.0, "avg_waste_kg": 0.0
    })
    proto = group_data.get("prototype", {
        "total_setups": 0, "avg_setup_time_mins": 0.0, "defect_rate_pct": 0.0,
        "pass_rate_pct": 0.0, "rework_rate_pct": 0.0, "avg_waste_kg": 0.0
    })

    # Metric calculations
    b_time = base["avg_setup_time_mins"]
    p_time = proto["avg_setup_time_mins"]
    setup_time_reduction_pct = round(((b_time - p_time) / b_time * 100.0), 2) if b_time > 0 else 0.0

    b_def = base["defect_rate_pct"]
    p_def = proto["defect_rate_pct"]
    defect_abs_reduction = round((b_def - p_def), 2)
    defect_pct_reduction = round(((b_def - p_def) / b_def * 100.0), 2) if b_def > 0 else 0.0

    b_rework = base["rework_rate_pct"]
    p_rework = proto["rework_rate_pct"]
    rework_reduction_pct = round(((b_rework - p_rework) / b_rework * 100.0), 2) if b_rework > 0 else 0.0

    b_waste = base["avg_waste_kg"]
    p_waste = proto["avg_waste_kg"]
    waste_reduction_pct = round(((b_waste - p_waste) / b_waste * 100.0), 2) if b_waste > 0 else 0.0

    # Per-variant breakdown
    cursor.execute("""
        SELECT 
            s.product_variant,
            s.is_prototype,
            AVG(s.setup_time_minutes) as avg_time,
            SUM(CASE WHEN fpi.pass_fail = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as defect_rate
        FROM setups s
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        GROUP BY s.product_variant, s.is_prototype
    """)
    variant_rows = cursor.fetchall()
    
    variant_breakdown = {}
    for vr in variant_rows:
        v_name = vr["product_variant"]
        if v_name not in variant_breakdown:
            variant_breakdown[v_name] = {}
        g_key = "prototype" if vr["is_prototype"] == 1 else "baseline"
        variant_breakdown[v_name][g_key] = {
            "avg_time": round(vr["avg_time"], 1),
            "defect_rate": round(vr["defect_rate"], 1)
        }

    conn.close()

    return {
        "disclaimer": SAFETY_DISCLAIMER,
        "baseline": base,
        "prototype": proto,
        "metrics": {
            "setup_time_improvement_pct": setup_time_reduction_pct,
            "first_piece_defect_abs_reduction_pct": defect_abs_reduction,
            "first_piece_defect_pct_reduction": defect_pct_reduction,
            "rework_reduction_pct": rework_reduction_pct,
            "waste_reduction_pct": waste_reduction_pct
        },
        "variant_breakdown": variant_breakdown
    }

if __name__ == "__main__":
    res = run_experiment_analysis()
    b = res['baseline']
    p = res['prototype']
    m = res['metrics']
    print("\nBaseline vs Prototype Experiment\n")
    print(f"{'Metric':<30} {'Baseline':<12} {'Prototype':<12} {'Improvement':<12}")
    print("-" * 68)
    print(f"{'Average Setup Time':<30} {b['avg_setup_time_mins']:.2f} min    {p['avg_setup_time_mins']:.2f} min    {m['setup_time_improvement_pct']:.2f}%")
    print(f"{'First-Piece Defect Rate':<30} {b['defect_rate_pct']:.2f}%     {p['defect_rate_pct']:.2f}%      {m['first_piece_defect_pct_reduction']:.2f}%")
    print(f"{'Average Material Waste':<30} {b['avg_waste_kg']:.2f} kg     {p['avg_waste_kg']:.2f} kg      {m['waste_reduction_pct']:.2f}%")
    print(f"{'Rework Rate':<30} {b['rework_rate_pct']:.2f}%     {p['rework_rate_pct']:.2f}%      {m['rework_reduction_pct']:.2f}%\n")
