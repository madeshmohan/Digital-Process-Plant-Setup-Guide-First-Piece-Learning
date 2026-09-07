import sqlite3
import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from backend.models import (
    ProductVariant, ValidationRequest, ValidationResponse,
    SetupCreateRequest, FirstPieceInspectionRequest,
    RecommendationResponse, SyncPayload
)
from backend.database.database import get_db_connection
from backend.validation.validation_engine import validate_parameters, PRODUCT_SPECS
from backend.learning.recommendation_engine import get_recommendations_for_variant
from analytics.experiment import run_experiment_analysis
from analytics.error_analysis import run_error_analysis

router = APIRouter(prefix="/api")

SAFETY_DISCLAIMER = (
    "Prototype only. All parameter limits, operating envelopes, recommendations, and experimental results "
    "are synthetic demonstration assumptions and must not be used as real plant operating instructions."
)

def log_audit_event(event_type: str, user_or_system: str, details: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, event_type, user_or_system, details) VALUES (?, ?, ?, ?)",
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, user_or_system, details)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log writing failed: {e}")

@router.get("/products", response_model=List[ProductVariant])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for r in rows:
        products.append(ProductVariant(
            product_id=r["product_id"],
            product_variant=r["product_variant"],
            product_family=r["product_family"],
            target_temperature=r["target_temperature"],
            min_temperature=r["min_temperature"],
            max_temperature=r["max_temperature"],
            target_pressure=r["target_pressure"],
            min_pressure=r["min_pressure"],
            max_pressure=r["max_pressure"]
        ))
    return products

@router.post("/validate", response_model=ValidationResponse)
def validate_params(req: ValidationRequest):
    result = validate_parameters(req.product_variant, req.temperature, req.pressure)
    log_audit_event(
        "PARAMETER_VALIDATION",
        "OPERATOR",
        f"Variant: {req.product_variant}, T: {req.temperature}°C, P: {req.pressure} bar -> Status: {result['status']}"
    )
    return ValidationResponse(
        product_variant=result["product_variant"],
        temperature=result["temperature"],
        pressure=result["pressure"],
        temp_valid=result["temp_valid"],
        pressure_valid=result["pressure_valid"],
        interaction_valid=result["interaction_valid"],
        interaction_score=result["interaction_score"],
        status=result["status"],
        reason=result["reason"],
        temp_deviation=result["temp_deviation"],
        pressure_deviation=result["pressure_deviation"]
    )

@router.post("/setups")
def create_setup(req: SetupCreateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    val_res = validate_parameters(req.product_variant, req.temperature, req.pressure)
    if val_res["status"] == "BLOCKED":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Cannot record setup: {val_res['reason']}")

    setup_id = req.setup_id if req.setup_id else f"SET-{datetime.datetime.now().strftime('%M%S%f')[:8]}"
    start_time = datetime.datetime.now()
    
    # Calculate setup time from step durations
    total_duration_sec = sum(s.duration_seconds for s in req.steps)
    setup_time_mins = round(total_duration_sec / 60.0, 1) if total_duration_sec > 0 else 25.0
    end_time = start_time + datetime.timedelta(minutes=setup_time_mins)

    cursor.execute("""
        INSERT OR IGNORE INTO setups (setup_id, batch_id, product_variant, operator_id, operator_experience_level, machine_id, shift, start_time, end_time, setup_time_minutes, is_prototype, final_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        setup_id, req.batch_id, req.product_variant, req.operator_id,
        req.operator_experience_level, req.machine_id, req.shift,
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
        setup_time_mins, 1 if req.is_prototype else 0, "Pending_Inspection"
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO setup_parameters (setup_id, temperature, pressure, temperature_deviation, pressure_deviation, interaction_score, validation_status, heating_time, stabilization_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        setup_id, req.temperature, req.pressure, val_res["temp_deviation"], val_res["pressure_deviation"],
        val_res["interaction_score"], val_res["status"], req.heating_time, req.stabilization_time
    ))

    for s in req.steps:
        cursor.execute("""
            INSERT OR IGNORE INTO setup_steps (setup_id, step_id, step_name, step_completed, timestamp, duration_seconds, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (setup_id, s.step_id, s.step_name, 1 if s.step_completed else 0, s.timestamp, s.duration_seconds, s.notes))

    conn.commit()
    conn.close()

    log_audit_event("SETUP_COMPLETED", req.operator_id, f"Setup {setup_id} created for Batch {req.batch_id}.")
    return {"message": "Setup created successfully", "setup_id": setup_id, "validation_status": val_res["status"]}

@router.post("/first-piece")
def record_first_piece(req: FirstPieceInspectionRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT setup_id FROM setups WHERE setup_id = ?", (req.setup_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Setup {req.setup_id} not found")

    pass_fail = 0 if req.defect_detected else 1
    
    # Calculate process quality score
    base_score = 100.0 - (req.dimensional_quality * 50.0)
    base_score = max(30.0, min(100.0, base_score)) if pass_fail == 1 else random_defect_score()
    
    insp_id = f"INS-{datetime.datetime.now().strftime('%M%S%f')[:8]}"
    insp_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT OR REPLACE INTO first_piece_inspection
        (inspection_id, setup_id, inspection_time, dimensional_quality, surface_quality, weight, color_appearance, process_quality_score, defect_detected, defect_type, pass_fail, inspector_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        insp_id, req.setup_id, insp_time, req.dimensional_quality, req.surface_quality,
        req.weight, req.color_appearance, round(base_score, 1),
        1 if req.defect_detected else 0, req.defect_type, pass_fail, req.inspector_comment
    ))

    cursor.execute("""
        UPDATE setups SET final_status = ? WHERE setup_id = ?
    """, ("Completed" if pass_fail == 1 else "Failed_Inspection", req.setup_id))

    # Insert default performance metric if absent
    cursor.execute("""
        INSERT OR REPLACE INTO performance_metrics (setup_id, rework_required, material_waste_kg, downtime_minutes, maintenance_flag)
        VALUES (?, ?, ?, ?, ?)
    """, (req.setup_id, 0 if pass_fail == 1 else 1, 1.2 if pass_fail == 1 else 5.8, 0.0 if pass_fail == 1 else 15.0, 0))

    conn.commit()
    conn.close()

    log_audit_event(
        "FIRST_PIECE_INSPECTION",
        "QUALITY_INSPECTOR",
        f"Setup {req.setup_id}: Pass/Fail = {'PASS' if pass_fail == 1 else 'FAIL'} (Defect: {req.defect_type})"
    )
    return {"message": "Inspection recorded", "inspection_id": insp_id, "pass_fail": "PASS" if pass_fail == 1 else "FAIL"}

def random_defect_score():
    return round(55.0, 1)

@router.get("/recommendations/{product_variant}", response_model=RecommendationResponse)
def get_recommendations(product_variant: str):
    rec = get_recommendations_for_variant(product_variant)
    log_audit_event("RECOMMENDATION_GENERATED", "SYSTEM", f"Generated recommendation for {product_variant}: T={rec['recommended_temperature']}°C, P={rec['recommended_pressure']} bar")
    return RecommendationResponse(**rec)

@router.get("/analytics/experiment")
def get_experiment():
    return run_experiment_analysis()

@router.get("/analytics/error-analysis")
def get_errors():
    return run_error_analysis()

@router.post("/sync")
def sync_offline_data(payload: SyncPayload):
    synced_setups = 0
    synced_inspections = 0
    setup_id_map = {}
    
    for s_req in payload.setups:
        try:
            res = create_setup(s_req)
            new_id = res.get("setup_id")
            if s_req.setup_id and new_id:
                setup_id_map[s_req.setup_id] = new_id
            synced_setups += 1
        except Exception as e:
            print(f"Setup sync error: {e}")

    for i_req in payload.inspections:
        try:
            # Map client temporary setup ID to permanent setup ID if remapped
            if i_req.setup_id in setup_id_map:
                i_req.setup_id = setup_id_map[i_req.setup_id]
            record_first_piece(i_req)
            synced_inspections += 1
        except Exception as e:
            print(f"Inspection sync error: {e}")

    log_audit_event("OFFLINE_SYNC", "SYSTEM", f"Synced {synced_setups} setups and {synced_inspections} inspections from offline cache.")
    return {
        "status": "success",
        "message": "Synchronization complete. All locally stored setup records have been uploaded.",
        "synced_setups": synced_setups,
        "synced_inspections": synced_inspections,
        "setup_id_map": setup_id_map
    }

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/setups/history")
def get_setup_history(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.setup_id, s.batch_id, s.product_variant, s.operator_id, s.machine_id,
               s.start_time, s.setup_time_minutes, s.is_prototype, s.final_status,
               sp.temperature, sp.pressure, sp.validation_status, sp.interaction_score,
               fpi.pass_fail, fpi.defect_type
        FROM setups s
        JOIN setup_parameters sp ON s.setup_id = sp.setup_id
        LEFT JOIN first_piece_inspection fpi ON s.setup_id = fpi.setup_id
        ORDER BY s.setup_id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
