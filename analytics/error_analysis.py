from typing import Dict, Any, List
from backend.database.database import get_db_connection

SAFETY_DISCLAIMER = (
    "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results "
    "are synthetic demonstration assumptions and must not be used as real plant operating instructions."
)

def run_error_analysis() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query all failed inspections or blocked parameters
    cursor.execute("""
        SELECT 
            s.setup_id,
            s.product_variant,
            s.machine_id,
            s.is_prototype,
            sp.temperature,
            sp.pressure,
            sp.validation_status,
            sp.interaction_score,
            fpi.defect_type,
            fpi.pass_fail,
            fpi.inspector_comment,
            pm.maintenance_flag
        FROM setups s
        JOIN setup_parameters sp ON s.setup_id = sp.setup_id
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        JOIN performance_metrics pm ON s.setup_id = pm.setup_id
        WHERE fpi.pass_fail = 0 OR sp.validation_status = 'BLOCKED'
    """)
    rows = cursor.fetchall()

    categories = {
        "Temperature Range Violation": 0,
        "Pressure Range Violation": 0,
        "Temperature-Pressure Interaction Violation": 0,
        "Operator Step Deviation": 0,
        "Equipment Drift": 0,
        "Other Material/Process Defect": 0
    }

    sample_failures = []

    for r in rows:
        val_stat = r["validation_status"]
        def_type = r["defect_type"]
        maint = r["maintenance_flag"]

        if val_stat == "BLOCKED":
            if r["interaction_score"] > 1.0 and (r["temperature"] > 0 and r["pressure"] > 0):
                category = "Temperature-Pressure Interaction Violation"
            elif "temp" in def_type.lower() or r["temperature"] < 170 or r["temperature"] > 225:
                category = "Temperature Range Violation"
            else:
                category = "Pressure Range Violation"
        elif maint == 1:
            category = "Equipment Drift"
        elif def_type == "interaction_stress_defect":
            category = "Temperature-Pressure Interaction Violation"
        elif def_type in ["dimensional_variation", "surface_defect"]:
            category = "Operator Step Deviation"
        else:
            category = "Other Material/Process Defect"

        categories[category] += 1

        if len(sample_failures) < 5:
            sample_failures.append({
                "setup_id": r["setup_id"],
                "variant": r["product_variant"],
                "machine": r["machine_id"],
                "is_prototype": bool(r["is_prototype"]),
                "temperature": r["temperature"],
                "pressure": r["pressure"],
                "validation_status": val_stat,
                "defect_type": def_type,
                "category": category,
                "comment": r["inspector_comment"]
            })

    total_errors = sum(categories.values())
    breakdown = []
    for cat, count in categories.items():
        pct = round((count / total_errors * 100.0), 1) if total_errors > 0 else 0.0
        breakdown.append({"category": cat, "count": count, "percentage": pct})

    # Maintenance Signals Detection
    cursor.execute("""
        SELECT machine_id, COUNT(*) as drift_count
        FROM setups s
        JOIN performance_metrics pm ON s.setup_id = pm.setup_id
        WHERE pm.maintenance_flag = 1
        GROUP BY machine_id
        HAVING drift_count >= 5
    """)
    maint_rows = cursor.fetchall()
    maintenance_signals = []
    for mr in maint_rows:
        maintenance_signals.append({
            "machine_id": mr["machine_id"],
            "drift_count": mr["drift_count"],
            "signal": f"Repeated parameter deviation detected on Machine {mr['machine_id']} ({mr['drift_count']} instances). Maintenance inspection recommended."
        })

    conn.close()

    return {
        "disclaimer": SAFETY_DISCLAIMER,
        "total_failures_analyzed": total_errors,
        "category_breakdown": breakdown,
        "sample_failures": sample_failures,
        "maintenance_signals": maintenance_signals
    }

if __name__ == "__main__":
    res = run_error_analysis()
    print("--- ERROR ANALYSIS ---")
    print(f"Total failures analyzed: {res['total_failures_analyzed']}")
    for cat in res['category_breakdown']:
        print(f" - {cat['category']}: {cat['count']} ({cat['percentage']}%)")
