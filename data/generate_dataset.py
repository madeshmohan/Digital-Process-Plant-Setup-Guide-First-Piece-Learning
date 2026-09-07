import os
import sqlite3
import random
import datetime
import pandas as pd
import numpy as np
from backend.database.database import get_db_connection, init_db, seed_default_products
from backend.validation.validation_engine import PRODUCT_SPECS, validate_parameters

def generate_synthetic_data(num_records=750):
    init_db()
    seed_default_products()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing non-product data for fresh seed
    cursor.execute("DELETE FROM audit_logs")
    cursor.execute("DELETE FROM performance_metrics")
    cursor.execute("DELETE FROM first_piece_inspection")
    cursor.execute("DELETE FROM setup_steps")
    cursor.execute("DELETE FROM setup_parameters")
    cursor.execute("DELETE FROM setups")
    conn.commit()

    random.seed(42)
    np.random.seed(42)

    variants = list(PRODUCT_SPECS.keys())
    operators = [
        ("OP-101", "Expert"), ("OP-102", "Intermediate"), ("OP-103", "Novice"),
        ("OP-104", "Expert"), ("OP-105", "Intermediate"), ("OP-106", "Novice"),
        ("OP-107", "Intermediate"), ("OP-108", "Novice")
    ]
    machines = ["M01", "M02", "M03", "M04"]
    shifts = ["Shift 1 (Morning)", "Shift 2 (Evening)", "Shift 3 (Night)"]
    
    defect_types = [
        "dimensional_variation", "surface_defect", "weight_variation", 
        "incomplete_formation", "discoloration", "interaction_stress_defect"
    ]

    setup_records = []
    param_records = []
    step_records = []
    inspection_records = []
    metric_records = []

    start_date = datetime.datetime(2026, 1, 1, 8, 0, 0)

    for i in range(1, num_records + 1):
        setup_id = f"SET-{1000 + i}"
        batch_id = f"BAT-{2000 + (i % 80)}"
        variant = random.choice(variants)
        spec = PRODUCT_SPECS[variant]
        op_id, op_exp = random.choice(operators)
        machine_id = random.choice(machines)
        shift = random.choice(shifts)

        # Baseline vs Prototype allocation (~45% Baseline, ~55% Prototype)
        is_prototype = 1 if i > 340 else 0

        # Machine M01 has occasional pressure drift for maintenance signal demo
        has_machine_drift = (machine_id == "M01" and random.random() < 0.35)

        if is_prototype == 0:
            # MANUAL BASELINE
            # Operator chooses parameters with higher variance and potential drift
            temp_noise = np.random.normal(0, 3.8)
            press_noise = np.random.normal(0, 0.28)
            if has_machine_drift:
                press_noise += 0.35

            actual_temp = spec["target_temperature"] + temp_noise
            actual_press = spec["target_pressure"] + press_noise

            # Setup time is longer for baseline: 35-55 mins
            setup_time_mins = round(random.uniform(35.0, 52.0) - (5.0 if op_exp == "Expert" else 0.0), 1)
        else:
            # DIGITAL PROTOTYPE
            # Validation guided setup: parameters stay tight around recommended/target values
            temp_noise = np.random.normal(0, 1.1)
            press_noise = np.random.normal(0, 0.08)
            
            # Small percentage (~5%) of intented invalid attempts that operator had to correct or test
            if random.random() < 0.05:
                temp_noise += random.choice([-8.0, 8.0])

            actual_temp = spec["target_temperature"] + temp_noise
            actual_press = spec["target_pressure"] + press_noise

            # Setup time is shorter for prototype: 22-34 mins
            setup_time_mins = round(random.uniform(22.0, 33.0) - (4.0 if op_exp == "Expert" else 0.0), 1)

        val_res = validate_parameters(variant, actual_temp, actual_press)
        val_status = val_res["status"]

        # Timestamps
        setup_start = start_date + datetime.timedelta(minutes=i * 35)
        setup_end = setup_start + datetime.timedelta(minutes=setup_time_mins)
        start_str = setup_start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = setup_end.strftime("%Y-%m-%d %H:%M:%S")

        # Determine First Piece Inspection Quality & Pass/Fail
        # Quality depends strongly on parameter validation status + operator experience
        if val_status == "VALID":
            fail_prob = 0.04 if is_prototype else 0.12
        elif val_status == "WARNING":
            fail_prob = 0.25 if is_prototype else 0.45
        else: # BLOCKED
            fail_prob = 0.92  # Out of envelope almost always fails or produces bad defect

        pass_first_piece = 0 if random.random() < fail_prob else 1

        if pass_first_piece == 1:
            defect_type = "None"
            dim_qual = round(random.uniform(0.01, 0.08), 3)  # mm deviation
            surf_qual = round(random.uniform(8.5, 9.9), 1)   # score out of 10
            weight_g = round(random.uniform(498.0, 502.0), 1)
            color_app = "Normal"
            quality_score = round(random.uniform(88.0, 99.0), 1)
            rework = 0
            waste_kg = round(random.uniform(0.5, 1.5), 2)
            comment = "First piece within specification parameters."
        else:
            if not val_res["temp_valid"]:
                defect_type = "discoloration" if actual_temp > spec["max_temperature"] else "incomplete_formation"
            elif not val_res["pressure_valid"]:
                defect_type = "dimensional_variation"
            elif not val_res["interaction_valid"]:
                defect_type = "interaction_stress_defect"
            else:
                defect_type = random.choice(defect_types)

            dim_qual = round(random.uniform(0.25, 0.85), 3)
            surf_qual = round(random.uniform(3.0, 6.5), 1)
            weight_g = round(random.uniform(485.0, 515.0), 1)
            color_app = "Discolored" if defect_type == "discoloration" else "Substandard"
            quality_score = round(random.uniform(40.0, 68.0), 1)
            rework = 1
            waste_kg = round(random.uniform(4.5, 12.0), 2)
            comment = f"Defect identified: {defect_type}. Parameter re-adjustment required."

        maint_flag = 1 if (has_machine_drift and val_res["pressure_deviation"] > 0.2) else 0

        # Save setup tuple
        final_status = "Completed" if pass_first_piece == 1 else "Failed_Inspection"
        setup_records.append((
            setup_id, batch_id, variant, op_id, op_exp, machine_id, shift,
            start_str, end_str, setup_time_mins, is_prototype, final_status
        ))

        param_records.append((
            setup_id, round(actual_temp, 2), round(actual_press, 2),
            val_res["temp_deviation"], val_res["pressure_deviation"],
            val_res["interaction_score"], val_status,
            round(random.uniform(8.0, 15.0), 1), round(random.uniform(5.0, 10.0), 1)
        ))

        # Setup steps
        step_names = [
            "Inspect machine condition", "Clean required contact surfaces", "Load required raw material",
            "Set target temperature", "Set target pressure", "Wait for thermal & pressure stabilization",
            "Verify actual parameters", "Run trial setup", "Perform first-piece inspection"
        ]
        step_time_cur = setup_start
        for s_idx, s_name in enumerate(step_names, start=1):
            dur_sec = random.randint(90, 360)
            step_time_cur += datetime.timedelta(seconds=dur_sec)
            step_records.append((
                setup_id, s_idx, s_name, 1, step_time_cur.strftime("%Y-%m-%d %H:%M:%S"), dur_sec, "Step verified"
            ))

        # First piece inspection record
        insp_id = f"INS-{1000 + i}"
        inspection_records.append((
            insp_id, setup_id, end_str, dim_qual, surf_qual, weight_g, color_app,
            quality_score, 0 if pass_first_piece == 1 else 1, defect_type, pass_first_piece, comment
        ))

        # Performance metric
        metric_records.append((
            setup_id, rework, waste_kg, round(random.uniform(5.0, 25.0) if rework else 0.0, 1), maint_flag
        ))

    # Insert into SQLite Database
    cursor.executemany("""
        INSERT INTO setups (setup_id, batch_id, product_variant, operator_id, operator_experience_level, machine_id, shift, start_time, end_time, setup_time_minutes, is_prototype, final_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, setup_records)

    cursor.executemany("""
        INSERT INTO setup_parameters (setup_id, temperature, pressure, temperature_deviation, pressure_deviation, interaction_score, validation_status, heating_time, stabilization_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, param_records)

    cursor.executemany("""
        INSERT INTO setup_steps (setup_id, step_id, step_name, step_completed, timestamp, duration_seconds, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, step_records)

    cursor.executemany("""
        INSERT INTO first_piece_inspection (inspection_id, setup_id, inspection_time, dimensional_quality, surface_quality, weight, color_appearance, process_quality_score, defect_detected, defect_type, pass_fail, inspector_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, inspection_records)

    cursor.executemany("""
        INSERT INTO performance_metrics (setup_id, rework_required, material_waste_kg, downtime_minutes, maintenance_flag)
        VALUES (?, ?, ?, ?, ?)
    """, metric_records)

    # Initial audit logs
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, event_type, user_or_system, details)
        VALUES (?, 'DATASET_GENERATED', 'SYSTEM', 'Synthetic dataset of 750 records seeded successfully.')
    """, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

    conn.commit()

    # Also export to CSV for data documentation
    df_setups = pd.read_sql_query("""
        SELECT s.setup_id, s.batch_id, s.product_variant, s.operator_id, s.operator_experience_level, s.machine_id, s.shift,
               s.setup_time_minutes, s.is_prototype, s.final_status,
               sp.temperature, sp.pressure, sp.temperature_deviation, sp.pressure_deviation, sp.interaction_score, sp.validation_status,
               fpi.pass_fail as first_piece_pass, fpi.defect_type, fpi.process_quality_score,
               pm.rework_required, pm.material_waste_kg, pm.maintenance_flag
        FROM setups s
        JOIN setup_parameters sp ON s.setup_id = sp.setup_id
        JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        JOIN performance_metrics pm ON s.setup_id = pm.setup_id
    """, conn)
    
    csv_path = os.path.join(os.path.dirname(__file__), "synthetic_dataset.csv")
    df_setups.to_csv(csv_path, index=False)

    conn.close()
    print(f"Generated synthetic dataset with {num_records} records.")
    print(f"Exported CSV to {csv_path}")

if __name__ == "__main__":
    generate_synthetic_data(750)
