import sqlite3
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "process_plant.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Products catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_variant TEXT UNIQUE NOT NULL,
        product_family TEXT NOT NULL,
        target_temperature REAL NOT NULL,
        min_temperature REAL NOT NULL,
        max_temperature REAL NOT NULL,
        target_pressure REAL NOT NULL,
        min_pressure REAL NOT NULL,
        max_pressure REAL NOT NULL
    );
    """)

    # Setups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setups (
        setup_id TEXT PRIMARY KEY,
        batch_id TEXT NOT NULL,
        product_variant TEXT NOT NULL,
        operator_id TEXT NOT NULL,
        operator_experience_level TEXT NOT NULL,
        machine_id TEXT NOT NULL,
        shift TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        setup_time_minutes REAL NOT NULL,
        is_prototype INTEGER NOT NULL DEFAULT 1,
        final_status TEXT NOT NULL
    );
    """)

    # Setup Parameters
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setup_parameters (
        setup_id TEXT PRIMARY KEY,
        temperature REAL NOT NULL,
        pressure REAL NOT NULL,
        temperature_deviation REAL NOT NULL,
        pressure_deviation REAL NOT NULL,
        interaction_score REAL NOT NULL,
        validation_status TEXT NOT NULL,
        heating_time REAL NOT NULL,
        stabilization_time REAL NOT NULL,
        FOREIGN KEY(setup_id) REFERENCES setups(setup_id)
    );
    """)

    # Setup Steps
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setup_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setup_id TEXT NOT NULL,
        step_id INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        step_completed INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY(setup_id) REFERENCES setups(setup_id)
    );
    """)

    # First Piece Inspection
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS first_piece_inspection (
        inspection_id TEXT PRIMARY KEY,
        setup_id TEXT NOT NULL UNIQUE,
        inspection_time TEXT NOT NULL,
        dimensional_quality REAL NOT NULL,
        surface_quality REAL NOT NULL,
        weight REAL NOT NULL,
        color_appearance TEXT NOT NULL,
        process_quality_score REAL NOT NULL,
        defect_detected INTEGER NOT NULL,
        defect_type TEXT,
        pass_fail INTEGER NOT NULL, -- 1 for Pass, 0 for Fail
        inspector_comment TEXT,
        FOREIGN KEY(setup_id) REFERENCES setups(setup_id)
    );
    """)

    # Performance & Maintenance Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance_metrics (
        setup_id TEXT PRIMARY KEY,
        rework_required INTEGER NOT NULL,
        material_waste_kg REAL NOT NULL,
        downtime_minutes REAL NOT NULL,
        maintenance_flag INTEGER NOT NULL,
        FOREIGN KEY(setup_id) REFERENCES setups(setup_id)
    );
    """)

    # Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        user_or_system TEXT NOT NULL,
        details TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def seed_default_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    products_data = [
        ("PROD-A", "Variant A", "Polymers", 180.0, 175.0, 185.0, 5.0, 4.7, 5.3),
        ("PROD-B", "Variant B", "Polymers", 195.0, 190.0, 200.0, 5.5, 5.2, 5.8),
        ("PROD-C", "Variant C", "Elastomers", 210.0, 205.0, 215.0, 6.0, 5.7, 6.3),
        ("PROD-D", "Variant D", "Elastomers", 220.0, 215.0, 225.0, 6.5, 6.2, 6.8),
    ]
    for row in products_data:
        cursor.execute("""
        INSERT OR REPLACE INTO products 
        (product_id, product_variant, product_family, target_temperature, min_temperature, max_temperature, target_pressure, min_pressure, max_pressure)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_default_products()
    print("Database initialized successfully.")
