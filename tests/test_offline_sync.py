import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.database import init_db, seed_default_products, get_db_connection

client = TestClient(app)

def setup_module(module):
    init_db()
    seed_default_products()

def test_offline_setup_creation_and_sync():
    # Test 1 & 2: Offline setup with client setup_id synced to backend
    offline_setup_id = "SET-OFFLINE-TEST-001"
    setup_payload = {
        "setup_id": offline_setup_id,
        "batch_id": "BAT-OFFLINE-001",
        "product_variant": "Variant A",
        "operator_id": "OP-101",
        "operator_experience_level": "Intermediate",
        "machine_id": "M01",
        "shift": "Shift 1 (Morning)",
        "is_prototype": True,
        "temperature": 180.0,
        "pressure": 5.0,
        "heating_time": 10.0,
        "stabilization_time": 5.0,
        "steps": [
            {
                "step_id": 1,
                "step_name": "Inspect machine condition",
                "step_completed": True,
                "timestamp": "2026-09-07T12:00:00",
                "duration_seconds": 120,
                "notes": "Offline step completed"
            }
        ]
    }

    sync_payload = {
        "setups": [setup_payload],
        "inspections": []
    }

    res = client.post("/api/sync", json=sync_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["synced_setups"] == 1

    # Verify record in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM setups WHERE setup_id = ?", (offline_setup_id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["batch_id"] == "BAT-OFFLINE-001"

def test_offline_inspection_relationship_sync():
    # Test 3: Synchronize first-piece inspection associated with offline setup ID
    offline_setup_id = "SET-OFFLINE-TEST-001"
    inspection_payload = {
        "setup_id": offline_setup_id,
        "dimensional_quality": 0.02,
        "surface_quality": 9.5,
        "weight": 500.0,
        "color_appearance": "Normal",
        "defect_detected": False,
        "defect_type": "None",
        "inspector_comment": "Offline inspection verified PASS"
    }

    sync_payload = {
        "setups": [],
        "inspections": [inspection_payload]
    }

    res = client.post("/api/sync", json=sync_payload)
    assert res.status_code == 200
    assert res.json()["synced_inspections"] == 1

    # Verify inspection record in database linked to setup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM first_piece_inspection WHERE setup_id = ?", (offline_setup_id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["pass_fail"] == 1

def test_sync_failure_handling_and_retry():
    # Test 4 & 5: Invalid/Blocked setup fails validation, retry with valid parameters succeeds
    invalid_setup_id = "SET-OFFLINE-BLOCKED-001"
    blocked_setup_payload = {
        "setup_id": invalid_setup_id,
        "batch_id": "BAT-BLOCKED-001",
        "product_variant": "Variant A",
        "operator_id": "OP-101",
        "operator_experience_level": "Novice",
        "machine_id": "M01",
        "shift": "Shift 1",
        "is_prototype": True,
        "temperature": 230.0,  # Out of range!
        "pressure": 5.0,
        "heating_time": 10.0,
        "stabilization_time": 5.0,
        "steps": []
    }

    # Attempting create_setup for blocked setup raises 400
    res_direct = client.post("/api/setups", json=blocked_setup_payload)
    assert res_direct.status_code == 400

    # Sync handles failure gracefully
    res_sync = client.post("/api/sync", json={"setups": [blocked_setup_payload], "inspections": []})
    assert res_sync.status_code == 200
    assert res_sync.json()["synced_setups"] == 0  # Blocked setup not synced

    # Correct parameters and retry
    corrected_setup_payload = dict(blocked_setup_payload)
    corrected_setup_payload["temperature"] = 180.0
    res_retry = client.post("/api/sync", json={"setups": [corrected_setup_payload], "inspections": []})
    assert res_retry.status_code == 200
    assert res_retry.json()["synced_setups"] == 1

def test_duplicate_sync_prevention():
    # Test 6: Attempt duplicate sync on an already synced setup ID
    offline_setup_id = "SET-OFFLINE-TEST-001"
    setup_payload = {
        "setup_id": offline_setup_id,
        "batch_id": "BAT-OFFLINE-001",
        "product_variant": "Variant A",
        "operator_id": "OP-101",
        "operator_experience_level": "Intermediate",
        "machine_id": "M01",
        "shift": "Shift 1 (Morning)",
        "is_prototype": True,
        "temperature": 180.0,
        "pressure": 5.0,
        "heating_time": 10.0,
        "stabilization_time": 5.0,
        "steps": []
    }

    res = client.post("/api/sync", json={"setups": [setup_payload], "inspections": []})
    assert res.status_code == 200

    # Verify setup count for this ID remains 1 (no duplicate row)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM setups WHERE setup_id = ?", (offline_setup_id,))
    count = cursor.fetchone()["count"]
    conn.close()
    assert count == 1
